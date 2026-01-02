const puppeteer = require('puppeteer');
const fs = require('fs');
const {execSync} = require('child_process');
const path = require('path');
const crypto = require('crypto');

// const imageUrls = [
//     'https://ipfs.io/ipfs/QmfC3THkEpnp5tNZesVLe1PJVc5eHUdvCcRHumFyqfWXgj',
//     'https://ipfs.io/ipfs/QmVAHYhcYN9T1aEurto4gfgdANiL79TRDuSMsMKTwbTKKs',
//     'https://ipfs.io/ipfs/Qmeqdu3gwazWns3wAisqt634XLBFhQHNmUjRmi3HnTXU8F',
//     'https://ipfs.io/ipfs/QmWLKoHaQ42xPcait723VpCok54SiEAuokMsdmLhfVA6pH',
//     'https://ipfs.io/ipfs/QmdmQRA5Lat8oQbx8MF2zryt1PTM6VMVyAfmGzwD3Xxdwx'
// ];

function getImageUrlsFromStdin() {
    let inputData = '';
    return new Promise((resolve, reject) => {
        process.stdin.on('data', chunk => {
            inputData += chunk;
        });
        process.stdin.on('end', () => {
            try {
                const urls = JSON.parse(inputData);
                resolve(urls);
            } catch (err) {
                reject(new Error("Failed to parse JSON input: " + err.message));
            }
        });
        process.stdin.on('error', reject);
    });
}

const uniqueId = crypto.randomUUID();
const framesDir = path.join(__dirname, `frames-${uniqueId}`);

const gifWidth = 552;
const gifHeight = 736;
const durationSeconds = 5;

// --- DUAL RATE CONFIGURATION ---
const frameDelayMs = 30;    // We still capture every 30ms (High resolution)
const captureFps = 33.33;   // (1000 / 30)

// CHANGE THIS: Lower value = Slower GIF.
// If it was "a bit" too fast, try 20-25. If it was "way" too fast, try 10-12.
const playbackFps = 30;

const totalFrames = durationSeconds * captureFps;
// Clean and create frames directory
if (!fs.existsSync(framesDir)) fs.mkdirSync(framesDir);

(async () => {
    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            '--disable-gpu',
            '--disable-software-rasterizer=false',
            '--disable-dev-shm-usage',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-frame-rate-limit',
            '--no-sandbox',
            //'--disable-setuid-sandbox',
            //'--disable-dev-shm-usage', // Critical for VPS environments
            //'--disable-accelerated-2d-canvas',
            //'--disable-gpu', // Let the browser use standard headless rendering
            //'--no-zygote',
            //'--single-process' // Reduces memory overhead on small droplets
        ]
    });
    const page = await browser.newPage();
    await page.setViewport({width: gifWidth, height: gifHeight});

    const imageUrls = await getImageUrlsFromStdin()
    const htmlContent = `
<html>
  <body style="
    margin: 0; 
    padding: 0; 
    /* Force the body to be exactly 380x600 as a baseline */
    width: 380px; 
    height: 600px;
    /* Allow it to expand ONLY up to the input sizes */
    max-width: ${gifWidth}px;
    max-height: ${gifHeight}px;
    background: transparent; 
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  ">
    ${imageUrls.map((url, i) => `
      <div style="
        position: absolute; 
        inset: 0; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        z-index: ${i};
      ">
        <img src="${url}" style="
          /* This ensures the image never exceeds the 380x600 box */
          /* unless the body itself is allowed to be larger */
          max-width: 100%; 
          max-height: 100%; 
          object-fit: contain;
        " />
      </div>
    `).join('')}
  </body>
</html>`;

    await page.setContent(htmlContent);

    // Ensure assets are loaded
    await page.evaluate(async () => {
        const imgs = Array.from(document.querySelectorAll('img'));
        await Promise.all(imgs.map(i => i.complete ? Promise.resolve() : new Promise(r => i.onload = r)));
    });

    const client = await page.target().createCDPSession();

    // Virtual Time ensures we don't drop frames during the 30ms "steps"
    await client.send('Emulation.setVirtualTimePolicy', {
        policy: 'advance',
        budget: totalFrames * frameDelayMs
    });


    for (let i = 0; i < totalFrames; i++) {
        const framePath = path.join(framesDir, `frame_${String(i).padStart(3, '0')}.png`);
        await page.screenshot({path: framePath, omitBackground: true});

        // Advance browser clock by 30ms
        await client.send('Emulation.setVirtualTimePolicy', {
            policy: 'advance',
            budget: frameDelayMs
        });
    }

    await browser.close();
    const gif = generateGif();
    if (gif) {
        process.stdout.write(gif);
    }
})();

function generateGif() {
    const palettePath = path.join(framesDir, 'palette.png');
    const gifPath = path.join(framesDir, 'stacked.gif');
    const firstFrame = path.join(framesDir, 'frame_000.png');
    const filterChain = `mpdecimate=hi=2000:lo=1000:frac=0.1,scale=${gifWidth}:${gifHeight}:force_original_aspect_ratio=decrease,pad=${gifWidth}:${gifHeight}:(ow-iw)/2:(oh-ih)/2:color=black@0`;

    try {
        // Step 1: Palette
        execSync(`"ffmpeg" -y -i "${firstFrame}" -vf "scale=${gifWidth}:${gifHeight}:force_original_aspect_ratio=decrease,pad=${gifWidth}:${gifHeight}:(ow-iw)/2:(oh-ih)/2:color=black@0,palettegen=max_colors=128" "${palettePath}"`);

        // Step 2: Render GIF
        execSync(`"ffmpeg" -y -framerate ${playbackFps} -i "${framesDir}/frame_%03d.png" -i "${palettePath}" -filter_complex "[0:v]${filterChain}[v];[v][1:v]paletteuse=dither=none:diff_mode=rectangle" -vsync vfr "${gifPath}"`);

        // Read the file into a Buffer (Bytes)
        const gifBuffer = fs.readFileSync(gifPath);

        // Cleanup temporary files
        if (fs.existsSync(framesDir)) fs.rmSync(framesDir, {recursive: true, force: true});

        return gifBuffer;
    } catch (err) {
        console.error('Optimization Error:', err.message);
        return null;
    }
}