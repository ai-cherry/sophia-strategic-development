const fs = require('fs');
const path = require('path');

function convertJsxToTsx(jsxContent, componentName) {
    // Add TypeScript imports
    let tsxContent = jsxContent;

    // Replace React import if needed
    tsxContent = tsxContent.replace(
        "import React from 'react'",
        "import React from 'react'"
    );

    // Add type annotations to function components
    tsxContent = tsxContent.replace(
        /function\s+(\w+)\s*\((.*?)\)\s*{/g,
        (match, name, params) => {
            if (params.trim() === '') {
                return `function ${name}(): React.ReactElement {`;
            } else {
                return `function ${name}(${params}: any): React.ReactElement {`;
            }
        }
    );

    // Convert arrow functions
    tsxContent = tsxContent.replace(
        /const\s+(\w+)\s*=\s*\((.*?)\)\s*=>\s*{/g,
        (match, name, params) => {
            if (params.trim() === '') {
                return `const ${name}: React.FC = () => {`;
            } else {
                return `const ${name}: React.FC<any> = (${params}) => {`;
            }
        }
    );

    // Add basic type annotations to useState
    tsxContent = tsxContent.replace(
        /useState\((.*?)\)/g,
        (match, initialValue) => {
            if (initialValue === 'null' || initialValue === 'undefined') {
                return `useState<any>(${initialValue})`;
            } else if (initialValue.startsWith('[') || initialValue.startsWith('{')) {
                return `useState<any>(${initialValue})`;
            } else if (initialValue === 'true' || initialValue === 'false') {
                return `useState<boolean>(${initialValue})`;
            } else if (!isNaN(initialValue)) {
                return `useState<number>(${initialValue})`;
            } else if (initialValue.startsWith("'") || initialValue.startsWith('"')) {
                return `useState<string>(${initialValue})`;
            }
            return match;
        }
    );

    return tsxContent;
}

module.exports = { convertJsxToTsx };
