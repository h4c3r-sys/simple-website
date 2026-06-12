const fs = require('fs');
const path = require('path');
const https = require('https');

const PFP_DIR = path.join(__dirname, '../public/pfps');

// Ensure directory exists
if (!fs.existsSync(PFP_DIR)) {
  fs.mkdirSync(PFP_DIR, { recursive: true });
}

// Clear existing un-categorized images
const existingFiles = fs.readdirSync(PFP_DIR);
for (const file of existingFiles) {
  if (file !== 'default.png') {
    fs.unlinkSync(path.join(PFP_DIR, file));
  }
}

const CATEGORIES = ['cars', 'football', 'anime', 'memes', 'nature', 'abstract', 'animals'];
const IMAGES_PER_CATEGORY = 100;

const downloadImage = (url, filepath) => {
  return new Promise((resolve, reject) => {
    // Add a randomized user agent and cache buster to bypass aggressive caching
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      }
    };

    https.get(url, options, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return downloadImage(res.headers.location, filepath).then(resolve).catch(reject);
      }

      if (res.statusCode !== 200) {
        reject(new Error(`Failed to get '${url}' (${res.statusCode})`));
        return;
      }

      const file = fs.createWriteStream(filepath);
      res.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(filepath, () => {});
      reject(err);
    });
  });
};

async function main() {
  console.log('Downloading Highly-Targeted PFPs...');

  // Download default PFP
  try {
    await downloadImage('https://ui-avatars.com/api/?name=Anon&background=random', path.join(PFP_DIR, 'default.png'));
    console.log('Downloaded default.png');
  } catch (e) {
    console.error('Failed to download default.png', e);
  }

  let totalDownloaded = 0;

  for (const category of CATEGORIES) {
    console.log(`Starting category: ${category}`);
    for (let i = 0; i < IMAGES_PER_CATEGORY; i++) {
      const filename = `pfp_${category}_${i}.jpg`;
      const filepath = path.join(PFP_DIR, filename);

      // LoremFlickr supports exact keywords for images (e.g. /anime, /cars)
      // The `?lock=` query forces it to give a unique image for each index instead of a cached one.
      const url = `https://loremflickr.com/150/150/${category}?lock=${i}`;

      try {
        await downloadImage(url, filepath);
        totalDownloaded++;
        if (totalDownloaded % 10 === 0) {
           console.log(`Downloaded ${totalDownloaded} images...`);
        }
      } catch (err) {
        console.error(`Failed to download ${filename}:`, err.message);
      }

      // Delay to respect API limits
      await new Promise(r => setTimeout(r, 200));
    }
  }

  console.log(`\nFinished successfully downloading ${totalDownloaded} categorized images.`);
  process.exit(0); // Force clean exit to prevent event-loop hangs
}

main();
