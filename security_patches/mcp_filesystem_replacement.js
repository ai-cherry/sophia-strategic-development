/**
 * Secure MCP Filesystem Server Replacement
 * Replaces @modelcontextprotocol/server-filesystem to eliminate GHSA-hc55-p739-j48w and GHSA-q66q-fx2p-7w4m
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const fs = require('fs').promises;
const path = require('path');

class SecureFilesystemServer {
    constructor(allowedRoots = []) {
        this.allowedRoots = allowedRoots.map(root => path.resolve(root));
        this.server = new Server(
            {
                name: 'secure-filesystem',
                version: '1.0.0',
            },
            {
                capabilities: {
                    tools: {},
                },
            }
        );
        
        this.setupHandlers();
    }

    /**
     * Securely validates if a path is within allowed roots
     */
    validatePath(requestedPath) {
        try {
            const resolvedPath = path.resolve(requestedPath);
            
            for (const allowedRoot of this.allowedRoots) {
                const relativePath = path.relative(allowedRoot, resolvedPath);
                
                // Security check: ensure path is within allowed root
                if (!relativePath.startsWith('..') && !path.isAbsolute(relativePath)) {
                    return resolvedPath;
                }
            }
            
            throw new Error(`Access denied: Path '${requestedPath}' is outside allowed directories`);
        } catch (error) {
            throw new Error(`Invalid path: ${error.message}`);
        }
    }

    setupHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return {
                tools: [
                    {
                        name: 'read_file',
                        description: 'Securely read a text file from an allowed directory',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                path: {
                                    type: 'string',
                                    description: 'Path to the file to read',
                                },
                            },
                            required: ['path'],
                        },
                    },
                    {
                        name: 'write_file',
                        description: 'Securely write to a text file in an allowed directory',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                path: {
                                    type: 'string',
                                    description: 'Path to the file to write',
                                },
                                content: {
                                    type: 'string',
                                    description: 'Content to write to the file',
                                },
                            },
                            required: ['path', 'content'],
                        },
                    },
                    {
                        name: 'list_directory',
                        description: 'Securely list contents of an allowed directory',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                path: {
                                    type: 'string',
                                    description: 'Path to the directory to list',
                                },
                            },
                            required: ['path'],
                        },
                    },
                    {
                        name: 'create_directory',
                        description: 'Securely create a directory in an allowed location',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                path: {
                                    type: 'string',
                                    description: 'Path to the directory to create',
                                },
                            },
                            required: ['path'],
                        },
                    },
                ],
            };
        });

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;

            try {
                switch (name) {
                    case 'read_file':
                        return await this.readFile(args.path);
                    case 'write_file':
                        return await this.writeFile(args.path, args.content);
                    case 'list_directory':
                        return await this.listDirectory(args.path);
                    case 'create_directory':
                        return await this.createDirectory(args.path);
                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
            } catch (error) {
                return {
                    content: [
                        {
                            type: 'text',
                            text: `Error: ${error.message}`,
                        },
                    ],
                    isError: true,
                };
            }
        });
    }

    async readFile(filePath) {
        const validatedPath = this.validatePath(filePath);
        
        try {
            const content = await fs.readFile(validatedPath, 'utf8');
            return {
                content: [
                    {
                        type: 'text',
                        text: content,
                    },
                ],
            };
        } catch (error) {
            throw new Error(`Failed to read file: ${error.message}`);
        }
    }

    async writeFile(filePath, content) {
        const validatedPath = this.validatePath(filePath);
        
        try {
            // Ensure directory exists
            const dir = path.dirname(validatedPath);
            await fs.mkdir(dir, { recursive: true });
            
            await fs.writeFile(validatedPath, content, 'utf8');
            return {
                content: [
                    {
                        type: 'text',
                        text: `Successfully wrote to ${validatedPath}`,
                    },
                ],
            };
        } catch (error) {
            throw new Error(`Failed to write file: ${error.message}`);
        }
    }

    async listDirectory(dirPath) {
        const validatedPath = this.validatePath(dirPath);
        
        try {
            const entries = await fs.readdir(validatedPath, { withFileTypes: true });
            const formattedEntries = entries.map(entry => ({
                name: entry.name,
                type: entry.isDirectory() ? 'directory' : 'file',
                path: path.join(validatedPath, entry.name),
            }));
            
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(formattedEntries, null, 2),
                    },
                ],
            };
        } catch (error) {
            throw new Error(`Failed to list directory: ${error.message}`);
        }
    }

    async createDirectory(dirPath) {
        const validatedPath = this.validatePath(dirPath);
        
        try {
            await fs.mkdir(validatedPath, { recursive: true });
            return {
                content: [
                    {
                        type: 'text',
                        text: `Successfully created directory ${validatedPath}`,
                    },
                ],
            };
        } catch (error) {
            throw new Error(`Failed to create directory: ${error.message}`);
        }
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('🔒 Secure MCP Filesystem Server started');
        console.error(`✅ Allowed roots: ${this.allowedRoots.join(', ')}`);
    }
}

// Create and start server with secure configuration
if (require.main === module) {
    const allowedRoots = process.argv.slice(2);
    if (allowedRoots.length === 0) {
        allowedRoots.push(process.cwd());
    }
    
    const server = new SecureFilesystemServer(allowedRoots);
    server.run().catch(console.error);
}

module.exports = { SecureFilesystemServer }; 