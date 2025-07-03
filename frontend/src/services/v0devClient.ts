/**
 * V0.dev Client - Frontend service for AI-driven UI component generation
 */

import { apiClient } from './apiClient';

export interface DesignContext {
  colors?: Record<string, string>;
  typography?: Record<string, string>;
  spacing?: Record<string, string>;
  components?: string[];
}

export interface ComponentGenerationRequest {
  prompt: string;
  designContext?: DesignContext;
  componentType?: 'react' | 'vue' | 'svelte';
  styling?: 'tailwind' | 'css-modules' | 'styled-components';
  typescript?: boolean;
  includeTests?: boolean;
}

export interface GeneratedComponent {
  componentCode: string;
  testCode?: string;
  metadata: {
    generatedAt: string;
    prompt: string;
    styling: string;
    typescript: boolean;
  };
}

export interface ComponentDeployment {
  status: 'pending' | 'success' | 'failed';
  deploymentId?: string;
  previewUrl?: string;
  error?: string;
}

class V0DevClient {
  private baseUrl = '/api/v1';

  /**
   * Generate a UI component from a prompt
   */
  async generateComponent(request: ComponentGenerationRequest): Promise<GeneratedComponent> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/chat`, {
        message: request.prompt,
        intent: 'UI_GENERATION',
        context: {
          designContext: request.designContext,
          componentType: request.componentType || 'react',
          styling: request.styling || 'tailwind',
          typescript: request.typescript !== false,
          includeTests: request.includeTests !== false
        }
      });

      if (!response.ok) {
        throw new Error(`Component generation failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data.result;
    } catch (error) {
      console.error('Error generating component:', error);
      throw error;
    }
  }

  /**
   * Stream component generation for live preview
   */
  async streamComponent(
    request: ComponentGenerationRequest,
    onChunk: (chunk: string) => void,
    onComplete?: () => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
          message: request.prompt,
          intent: 'UI_GENERATION',
          context: {
            designContext: request.designContext,
            stream: true
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Stream failed: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onComplete?.();
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.choices?.[0]?.delta?.content) {
                onChunk(parsed.choices[0].delta.content);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }

      onComplete?.();
    } catch (error) {
      console.error('Error streaming component:', error);
      onError?.(error as Error);
    }
  }

  /**
   * Deploy a component to Vercel
   */
  async deployComponent(
    projectId: string,
    componentCode: string,
    componentName: string,
    branch: string = 'feature/ui'
  ): Promise<ComponentDeployment> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/deploy/component`, {
        projectId,
        componentCode,
        componentName,
        branch
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Deployment failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Error deploying component:', error);
      throw error;
    }
  }

  /**
   * Get Figma design context for component generation
   */
  async getFigmaContext(fileId?: string): Promise<DesignContext> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/design/context`, {
        params: fileId ? { fileId } : undefined
      });

      if (!response.ok) {
        throw new Error('Failed to fetch design context');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching Figma context:', error);
      // Return empty context as fallback
      return {};
    }
  }

  /**
   * Generate multiple component variations
   */
  async generateVariations(
    basePrompt: string,
    variations: string[],
    designContext?: DesignContext
  ): Promise<GeneratedComponent[]> {
    const promises = variations.map(variation =>
      this.generateComponent({
        prompt: `${basePrompt} - Variation: ${variation}`,
        designContext
      })
    );

    return Promise.all(promises);
  }

  /**
   * Validate generated component code
   */
  async validateComponent(componentCode: string): Promise<{
    valid: boolean;
    errors?: string[];
    warnings?: string[];
  }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/validate/component`, {
        code: componentCode
      });

      if (!response.ok) {
        throw new Error('Validation failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Error validating component:', error);
      return {
        valid: false,
        errors: ['Failed to validate component']
      };
    }
  }

  /**
   * Get component generation history
   */
  async getGenerationHistory(limit: number = 10): Promise<GeneratedComponent[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/components/history`, {
        params: { limit }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching generation history:', error);
      return [];
    }
  }

  /**
   * Save component to library
   */
  async saveToLibrary(
    component: GeneratedComponent,
    metadata: {
      name: string;
      category?: string;
      tags?: string[];
      description?: string;
    }
  ): Promise<{ id: string; success: boolean }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/components/library`, {
        ...component,
        ...metadata
      });

      if (!response.ok) {
        throw new Error('Failed to save component');
      }

      return await response.json();
    } catch (error) {
      console.error('Error saving to library:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const v0devClient = new V0DevClient();

// Export types
export type { V0DevClient }; 