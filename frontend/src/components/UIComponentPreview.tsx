import React, { useState, useEffect, useMemo, Suspense } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Copy, Download, Eye, Code, Loader2, AlertCircle } from 'lucide-react';
import { v0devClient, GeneratedComponent } from '@/services/v0devClient';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface UIComponentPreviewProps {
  component?: GeneratedComponent;
  isLoading?: boolean;
  error?: string;
  onDeploy?: (componentCode: string, componentName: string) => void;
  onSaveToLibrary?: (component: GeneratedComponent) => void;
}

// Component skeleton loader
const ComponentSkeleton = () => (
  <div className="space-y-4 p-6">
    <Skeleton className="h-8 w-3/4" />
    <div className="space-y-2">
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <Skeleton className="h-4 w-4/6" />
    </div>
    <div className="flex gap-2">
      <Skeleton className="h-10 w-24" />
      <Skeleton className="h-10 w-24" />
    </div>
  </div>
);

// Safe component renderer using iframe
const SafeComponentRenderer: React.FC<{ code: string }> = ({ code }) => {
  const [error, setError] = useState<string | null>(null);

  const iframeContent = useMemo(() => {
    try {
      // Create a complete HTML document with the component
      return `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
          <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
          <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
          <script src="https://cdn.tailwindcss.com"></script>
          <style>
            body {
              margin: 0;
              padding: 16px;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: #f9fafb;
            }
            #root {
              background: white;
              border-radius: 8px;
              padding: 24px;
              box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
          </style>
        </head>
        <body>
          <div id="root"></div>
          <script type="text/babel">
            ${code}

            const App = () => {
              try {
                return <Component />;
              } catch (e) {
                return (
                  <div style={{color: 'red', padding: '20px'}}>
                    Error rendering component: {e.message}
                  </div>
                );
              }
            };

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
          </script>
        </body>
        </html>
      `;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to render component');
      return '';
    }
  }, [code]);

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full h-full min-h-[400px] border rounded-lg overflow-hidden">
      <iframe
        srcDoc={iframeContent}
        className="w-full h-full min-h-[400px]"
        sandbox="allow-scripts"
        title="Component Preview"
      />
    </div>
  );
};

export const UIComponentPreview: React.FC<UIComponentPreviewProps> = ({
  component,
  isLoading,
  error,
  onDeploy,
  onSaveToLibrary
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code' | 'test'>('preview');
  const [isCopied, setIsCopied] = useState(false);

  const handleCopyCode = async () => {
    if (!component?.componentCode) return;

    try {
      await navigator.clipboard.writeText(component.componentCode);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const handleDownloadCode = () => {
    if (!component?.componentCode) return;

    const blob = new Blob([component.componentCode], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Component.tsx';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDeploy = () => {
    if (!component?.componentCode || !onDeploy) return;

    const componentName = component.metadata.prompt
      .split(' ')
      .slice(0, 3)
      .map(w => w.charAt(0).toUpperCase() + w.slice(1))
      .join('');

    onDeploy(component.componentCode, componentName);
  };

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            Generating Component...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ComponentSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Generation Error</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!component) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Component Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            Generate a component to see the preview here
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Generated Component</CardTitle>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={handleCopyCode}
              disabled={!component.componentCode}
            >
              <Copy className="h-4 w-4 mr-1" />
              {isCopied ? 'Copied!' : 'Copy'}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleDownloadCode}
              disabled={!component.componentCode}
            >
              <Download className="h-4 w-4 mr-1" />
              Download
            </Button>
            {onDeploy && (
              <Button
                size="sm"
                onClick={handleDeploy}
                disabled={!component.componentCode}
              >
                Deploy to Vercel
              </Button>
            )}
            {onSaveToLibrary && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onSaveToLibrary(component)}
                disabled={!component.componentCode}
              >
                Save to Library
              </Button>
            )}
          </div>
        </div>
        <div className="text-sm text-muted-foreground mt-1">
          {component.metadata.prompt}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
          <TabsList className="mb-4">
            <TabsTrigger value="preview">
              <Eye className="h-4 w-4 mr-1" />
              Preview
            </TabsTrigger>
            <TabsTrigger value="code">
              <Code className="h-4 w-4 mr-1" />
              Code
            </TabsTrigger>
            {component.testCode && (
              <TabsTrigger value="test">
                Test Code
              </TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="preview" className="mt-0">
            <Suspense fallback={<ComponentSkeleton />}>
              <SafeComponentRenderer code={component.componentCode} />
            </Suspense>
          </TabsContent>

          <TabsContent value="code" className="mt-0">
            <div className="max-h-[600px] overflow-auto rounded-lg">
              <SyntaxHighlighter
                language="tsx"
                style={vscDarkPlus}
                customStyle={{
                  margin: 0,
                  borderRadius: '0.5rem'
                }}
              >
                {component.componentCode}
              </SyntaxHighlighter>
            </div>
          </TabsContent>

          {component.testCode && (
            <TabsContent value="test" className="mt-0">
              <div className="max-h-[600px] overflow-auto rounded-lg">
                <SyntaxHighlighter
                  language="tsx"
                  style={vscDarkPlus}
                  customStyle={{
                    margin: 0,
                    borderRadius: '0.5rem'
                  }}
                >
                  {component.testCode}
                </SyntaxHighlighter>
              </div>
            </TabsContent>
          )}
        </Tabs>

        <div className="mt-4 text-sm text-muted-foreground">
          <div className="flex flex-wrap gap-4">
            <span>Style: {component.metadata.styling}</span>
            <span>TypeScript: {component.metadata.typescript ? 'Yes' : 'No'}</span>
            <span>Generated: {new Date(component.metadata.generatedAt).toLocaleString()}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default UIComponentPreview;
