const puppeteer = require('puppeteer');
const path = require('path');
const {execSync} = require('child_process');
const {
    captureFps,
    defaultGifWidth,
    defaultGifHeight,
    frameDelayMs,
    playbackFps,
    defaultTraitWidth,
    defaultTraitHeight
} = require("../configs/Config");
const {readFilesAsStrings} = require('../utils/io/Files')

let browser

async function startBrowser() {
   browser = await puppeteer.launch({
        headless: "new",
        executablePath: '/usr/bin/chromium-browser',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-frame-rate-limit', '--disable-gpu']
    });
}

startBrowser()

/**
 * Returns the full path to a subdirectory inside the temp folder.
 */
async function generateGif(tempDir, maxT) {
    console.log(maxT)
    const totalFrames = Math.ceil(maxT * captureFps);
    console.log(totalFrames)
    const imageUrls = await readFilesAsStrings(tempDir)
    const resourcesDir = tempDir

    // Create an isolated incognito-like window
    const context = await browser.createBrowserContext();
    const page = await context.newPage();
    await page.setViewport({width: defaultGifWidth, height: defaultGifHeight});

    const htmlContent = `
    <html>
      <body style="margin:0; padding:0; width:${defaultGifWidth}px; height:${defaultGifHeight}px; background:transparent; overflow:hidden;">
        ${imageUrls.map((url, i) => `
          <div style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; z-index:${i};">
            <img src="${url}" style="width:100%; height:100%; object-fit:contain;" />
          </div>
        `).join('')}
      </body>
    </html>`;

    await page.setContent(htmlContent);

    // Image logic: Apply padding if aspect ratio isn't 3:4
    await page.evaluate(
        ({ defaultGifWidth, defaultGifHeight, defaultTraitWidth, defaultTraitHeight }) => {
            const xPadding = (defaultGifWidth - defaultTraitWidth) / 2;
            const yPadding = (defaultGifHeight - defaultTraitHeight) / 2;

            document.querySelectorAll('img').forEach(img => {
                const ratio = Math.round((img.naturalWidth / img.naturalHeight) * 100) / 100;
                if (Math.abs(ratio - 0.75) > 0.01) {
                    img.parentElement.style.padding = `${xPadding}px ${yPadding}px`;
                }
            });
        },
        { defaultGifWidth, defaultGifHeight, defaultTraitWidth, defaultTraitHeight } // pass as second argument
    );

    const client = await page.target().createCDPSession();
    await client.send('Emulation.setVirtualTimePolicy', {
        policy: 'pause',
    });

    // Capture Frames
    for (let i = 0; i <= totalFrames; i++) {
        const framePath = path.join(resourcesDir, `frame_${String(i).padStart(3, '0')}.png`);
        await page.screenshot({path: framePath, omitBackground: true});
        await client.send('Emulation.setVirtualTimePolicy', {
            policy: 'advance', budget: Number(frameDelayMs)
        });
    }

    await context.close(); // Closes tabs and clears memory

    // FFmpeg Processing
    const palettePath = path.join(resourcesDir, 'palette.png');
    const gifPath = path.join(resourcesDir, 'result.gif');

    try {
        // Generate Palette
        execSync(`ffmpeg -y -i "${path.join(resourcesDir, 'frame_000.png')}" -vf "palettegen=max_colors=256" "${palettePath}"`);
        // Generate Final GIF
        execSync(`ffmpeg -y -framerate ${playbackFps} -i "${resourcesDir}/frame_%03d.png" -i "${palettePath}" -filter_complex "[0:v]paletteuse=dither=none" "${gifPath}"`);

        return gifPath
    } catch (e) {
        throw e
    }
}

module.exports = {
    generateGif
};