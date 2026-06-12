const fs = require('fs');
const path = require('path');
const https = require('https');

const PFP_DIR = path.join(__dirname, '../public/pfps');

// Ensure directory exists
if (!fs.existsSync(PFP_DIR)) {
  fs.mkdirSync(PFP_DIR, { recursive: true });
}

const CATEGORIES = ['cars', 'football', 'anime', 'memes', 'nature', 'abstract', 'animals'];
const IMAGES_PER_CATEGORY = 100;

const downloadImage = (url, filepath) => {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
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
  console.log('Downloading PFPs...');

  // Download default PFP
  try {
    await downloadImage('https://ui-avatars.com/api/?name=Admin&background=random', path.join(PFP_DIR, 'default.png'));
    console.log('Downloaded default.png');
  } catch (e) {
    console.error('Failed to download default.png', e);
  }

  let index = 1;
  for (const category of CATEGORIES) {
    for (let i = 0; i < IMAGES_PER_CATEGORY; i++) {
      const filename = `pfp_${index}.jpg`;
      const filepath = path.join(PFP_DIR, filename);
      // We use picsum.photos with a seed based on category and index to get varied images
      const url = `https://picsum.photos/seed/${category}${i}/150/150`;

      try {
        await downloadImage(url, filepath);
        console.log(`Downloaded ${filename} (${category})`);
        index++;
      } catch (err) {
        console.error(`Failed to download ${filename}:`, err.message);
      }

      // Small delay to not overwhelm the service
      await new Promise(r => setTimeout(r, 100));
    }
  }

  console.log(`Finished downloading ${index - 1} images.`);
}

main();
