const sharp = require('C:/Users/Asus/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
sharp('frontend/public/linkguardian-logo.svg').resize(512,512).png().toFile('docs/assets/linkguardian-logo.png').catch(e => {console.error(e);process.exit(1)});
