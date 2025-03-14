#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const process = require('process');

function createFrontendScaffold(parent, structure) {
    Object.entries(structure).forEach(([name, content]) => {
        const fullPath = path.join(parent, name);
        if (typeof content === 'object') {
            fs.mkdirSync(fullPath, { recursive: true });
            createFrontendScaffold(fullPath, content);
        } else {
            fs.writeFileSync(fullPath, content || '', 'utf8');
        }
    });
}

function copyTemplateFiles(destination, templateDir) {
    const filesToCopy = ['.gitignore', 'package.json', 'live-server.config.js'];

    filesToCopy.forEach(file => {
        const src = path.join(templateDir, file);
        const dest = path.join(destination, file);

        if (fs.existsSync(src)) {
            fs.copyFileSync(src, dest);
            console.log(`Copied ${file} to ${destination}`);
        } else {
            console.warn(`Warning: ${file} not found in template directory '${templateDir}'`);
        }
    });
}

function setupNodeModules(destination) {
    try {
        console.log('Initializing npm project...');
        execSync('npm init -y', { cwd: destination, stdio: 'inherit' });

        console.log('Installing dependencies...');
        execSync('npm install jquery live-server', { cwd: destination, stdio: 'inherit' });
    } catch (error) {
        console.error('Error setting up dependencies:', error);
        process.exit(1);
    }
}

function main() {
    if (process.argv.length < 5) {
        console.error('Usage: node scaffolder.js <json_file> <destination> <template_directory>');
        process.exit(1);
    }

    const jsonFile = path.resolve(process.argv[2]);
    const destination = path.resolve(process.argv[3]);
    const templateDir = path.resolve(process.argv[4]);

    if (!fs.existsSync(jsonFile)) {
        console.error(`Error: File '${jsonFile}' does not exist.`);
        process.exit(1);
    }
    if (!fs.existsSync(templateDir)) {
        console.error(`Error: Template directory '${templateDir}' does not exist.`);
        process.exit(1);
    }

    let projectStructure;
    try {
        projectStructure = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));
    } catch (error) {
        console.error(`Error parsing JSON file '${jsonFile}':`, error);
        process.exit(1);
    }

    console.log(`Creating front-end project structure in ${destination}...`);
    createFrontendScaffold(destination, projectStructure);
    console.log('Project structure created successfully.');

    copyTemplateFiles(destination, templateDir);
    setupNodeModules(destination);
    console.log('Front-end project setup complete!');

    console.log('\nTo start development:');
    console.log('  cd ' + destination);
    console.log('  npm start (or configure your package.json for start scripts)');
}

main();
 

// node ./utils/javascript/scaffolder.js ./utils/javascript/template.json . ./utils/javascript
