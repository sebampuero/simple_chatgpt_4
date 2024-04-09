const fs = require('fs-extra');

// Paths
const buildPath = 'build';
const staticPath = '../static'; // Replace with your Sanic static folder path

// Copy build files to Sanic static folder
async function copyBuildFiles() {
  try {
    await fs.remove(staticPath);
    await fs.ensureDir(staticPath);
    await fs.copy(buildPath, staticPath);
    console.log('Build files copied successfully!');
  } catch (error) {
    console.error('Error copying build files:', error);
  }
}

// Run the script
copyBuildFiles();