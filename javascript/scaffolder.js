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

function setupNodeModules(destination) {
    try {
        console.log('Initializing npm project...');
        execSync('npm init -y', { cwd: destination, stdio: 'inherit' });
        
        console.log('Installing jQuery...');
        execSync('npm install jquery', { cwd: destination, stdio: 'inherit' });
    } catch (error) {
        console.error('Error setting up dependencies:', error);
        process.exit(1);
    }
}

function main() {
    if (process.argv.length < 3) {
        console.error('Usage: node scaffold.js <json_file> [destination]');
        process.exit(1);
    }
    
    const jsonFile = path.resolve(process.argv[2]);
    const destination = process.argv[3] ? path.resolve(process.argv[3]) : process.cwd();
    
    if (!fs.existsSync(jsonFile)) {
        console.error(`Error: File '${jsonFile}' does not exist.`);
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
    
    setupNodeModules(destination);
    console.log('Front-end project setup complete!');
    
    console.log('\nTo start development:');
    console.log('  cd ' + destination);
    console.log('  Open index.html in your browser');
}

main();


// node javascript/scaffolder.js javascript/template.json .                   
