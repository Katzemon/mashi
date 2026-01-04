const http = require('http');
const {PORT} = require('../configs/config');
const {generateGif} = require('../gif/GifMaker');


async function startServer() {
    http.createServer(async (req, res) => {
        if (req.method === 'POST') {
            let body = '';
            req.on('data', chunk => body += chunk);
            req.on('end', async () => {
                try {
                    const { tempDir, maxT} = JSON.parse(body);
                    const gifPath = await generateGif(tempDir, maxT);
                    res.writeHead(200, {'Content-Type': 'text/plain'});
                    res.end(gifPath);
                } catch (err) {
                    console.error("Internal Error:", err);
                    res.writeHead(500);
                    res.end(err.message);
                }
            });
        }
    }).listen(PORT, () => {
    });
}

module.exports = {
    startServer
};