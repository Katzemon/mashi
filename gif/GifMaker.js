const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const {execSync} = require('child_process');
const crypto = require('crypto');
const {
    captureFps,
    defaultGifWidth,
    defaultGifHeight,
    frameDelayMs,
    playbackFps,
    defaultTraitWidth,
    defaultTraitHeight
} = require("../configs/Config");

let browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-frame-rate-limit', '--disable-gpu']
});

async function generateGif(imageUrls, maxT) {
    const totalFrames = Math.ceil(maxT * captureFps);

    const uniqueId = crypto.randomUUID();
    const framesDir = path.join(__dirname, `frames-${uniqueId}`);
    if (!fs.existsSync(framesDir)) fs.mkdirSync(framesDir);

    // Create an isolated incognito-like window
    const context = await browser.createBrowserContext();
    const page = await context.newPage();
    await page.setViewport({width: defaultGifWidth, height: defaultGifHeight});

    const htmlContent = `
    <html>
      <body style="margin:0; padding:0; width:${gifWidth}px; height:${gifHeight}px; background:transparent; overflow:hidden;">
        ${imageUrls.map((url, i) => `
          <div style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; z-index:${i};">
            <img src="${url}" style="width:100%; height:100%; object-fit:contain;" />
          </div>
        `).join('')}
      </body>
    </html>`;

    await page.setContent(htmlContent);

    // Image logic: Apply padding if aspect ratio isn't 3:4
    await page.evaluate(() => {
        const xPadding = (defaultGifWidth - defaultTraitWidth) / 2
        const yPadding = (defaultGifHeight - defaultTraitHeight) / 2

        document.querySelectorAll('img').forEach(img => {
            const ratio = img.naturalWidth / img.naturalHeight;
            if (Math.abs(ratio - 0.75) > 0.01) {
                img.parentElement.style.padding = `${xPadding}px ${yPadding}px`;
            }
        });
    });

    const client = await page.target().createCDPSession();
    await client.send('Emulation.setVirtualTimePolicy', {
        policy: 'advance',
        budget: totalFrames * frameDelayMs
    });

    // Capture Frames
    for (let i = 0; i < totalFrames; i++) {
        const framePath = path.join(framesDir, `frame_${String(i).padStart(3, '0')}.png`);
        await page.screenshot({path: framePath, omitBackground: true});
        await client.send('Emulation.setVirtualTimePolicy', {
            policy: 'advance', budget: frameDelayMs
        });
    }

    await context.close(); // Closes tabs and clears memory

    // FFmpeg Processing
    const palettePath = path.join(framesDir, 'palette.png');
    const gifPath = path.join(framesDir, 'result.gif');

    try {
        // Generate Palette
        execSync(`ffmpeg -y -i "${path.join(framesDir, 'frame_000.png')}" -vf "palettegen=max_colors=256" "${palettePath}"`);
        // Generate Final GIF
        execSync(`ffmpeg -y -framerate ${playbackFps} -i "${framesDir}/frame_%03d.png" -i "${palettePath}" -filter_complex "[0:v]paletteuse=dither=none" "${gifPath}"`);

        const buffer = fs.readFileSync(gifPath);
        fs.rmSync(framesDir, {recursive: true, force: true});
        return buffer;
    } catch (e) {
        fs.rmSync(framesDir, {recursive: true, force: true});
        throw e;
    }
}

module.exports = {
    generateGif
};