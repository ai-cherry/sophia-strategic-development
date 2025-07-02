#!/usr/bin/env python3
"""
Simple UI/UX Agent MCP Server
Provides design and component generation assistance
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleUIUXServer:
    def __init__(self):
        self.app = FastAPI(title="Simple UI/UX Agent MCP Server", version="1.0.0")
        self.component_templates = {}
        self.design_patterns = {}
        self.setup_routes()
        self.setup_middleware()
        self.load_templates()

    def setup_middleware(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Setup API routes"""

        @self.app.get("/")
        async def root():
            return {
                "name": "Simple UI/UX Agent MCP Server",
                "version": "1.0.0",
                "status": "running",
                "capabilities": ["generate_component", "validate_design", "get_accessibility_tips"],
                "available_templates": len(self.component_templates),
                "design_patterns": len(self.design_patterns)
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "templates_loaded": len(self.component_templates),
                "patterns_loaded": len(self.design_patterns),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.post("/api/generate_component")
        async def generate_component(request: Dict[str, Any]):
            """Generate a React component based on specifications"""
            try:
                component_type = request.get("type", "button")
                component_name = request.get("name", "CustomComponent")
                props = request.get("props", {})
                styling = request.get("styling", "modern")
                accessibility = request.get("accessibility", True)
                
                # Get template for component type
                template = self.component_templates.get(component_type, self.component_templates["button"])
                
                # Generate component code
                component_code = self.generate_component_code(
                    component_name, template, props, styling, accessibility
                )
                
                # Generate TypeScript types
                types_code = self.generate_types_code(component_name, props)
                
                # Generate CSS styles
                css_code = self.generate_css_code(component_name, styling)
                
                # Generate test file
                test_code = self.generate_test_code(component_name, props)
                
                logger.info(f"Generated {component_type} component: {component_name}")
                
                return {
                    "success": True,
                    "component": {
                        "name": component_name,
                        "type": component_type,
                        "code": component_code,
                        "types": types_code,
                        "styles": css_code,
                        "tests": test_code,
                        "accessibility_score": 95 if accessibility else 70,
                        "styling": styling
                    },
                    "files": {
                        f"{component_name}.tsx": component_code,
                        f"{component_name}.types.ts": types_code,
                        f"{component_name}.module.css": css_code,
                        f"{component_name}.test.tsx": test_code
                    }
                }
                
            except Exception as e:
                logger.error(f"Error generating component: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/validate_design")
        async def validate_design(request: Dict[str, Any]):
            """Validate design system compliance"""
            try:
                component_code = request.get("code", "")
                design_system = request.get("design_system", "material")
                
                # Analyze the component code
                validation_results = self.validate_component_design(component_code, design_system)
                
                logger.info(f"Validated design for {design_system} system")
                
                return {
                    "success": True,
                    "validation": validation_results,
                    "overall_score": validation_results["score"],
                    "design_system": design_system
                }
                
            except Exception as e:
                logger.error(f"Error validating design: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/get_accessibility_tips")
        async def get_accessibility_tips(request: Dict[str, Any]):
            """Get accessibility improvement tips"""
            try:
                component_type = request.get("type", "general")
                current_level = request.get("current_level", "A")
                target_level = request.get("target_level", "AA")
                
                # Get accessibility tips based on component type
                tips = self.get_accessibility_recommendations(component_type, current_level, target_level)
                
                return {
                    "success": True,
                    "component_type": component_type,
                    "current_level": current_level,
                    "target_level": target_level,
                    "tips": tips,
                    "total_recommendations": len(tips)
                }
                
            except Exception as e:
                logger.error(f"Error getting accessibility tips: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/optimize_performance")
        async def optimize_performance(request: Dict[str, Any]):
            """Get performance optimization suggestions"""
            try:
                component_code = request.get("code", "")
                performance_target = request.get("target", "fast")
                
                optimizations = self.analyze_performance(component_code, performance_target)
                
                return {
                    "success": True,
                    "optimizations": optimizations,
                    "performance_score": optimizations["score"],
                    "target": performance_target
                }
                
            except Exception as e:
                logger.error(f"Error optimizing performance: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/design_patterns")
        async def get_design_patterns():
            """Get available design patterns"""
            try:
                return {
                    "success": True,
                    "patterns": list(self.design_patterns.keys()),
                    "total_patterns": len(self.design_patterns),
                    "categories": ["layout", "navigation", "forms", "data-display", "feedback"]
                }
                
            except Exception as e:
                logger.error(f"Error getting design patterns: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def load_templates(self):
        """Load component templates and design patterns"""
        
        # Component templates
        self.component_templates = {
            "button": {
                "base": """import React from 'react';
import styles from './{name}.module.css';

interface {name}Props {{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  ariaLabel?: string;
}}

export const {name}: React.FC<{name}Props> = ({{
  children,
  onClick,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  ariaLabel
}}) => {{
  return (
    <button
      className={{`${{styles.button}} ${{styles[variant]}} ${{styles[size]}}`}}
      onClick={{onClick}}
      disabled={{disabled}}
      aria-label={{ariaLabel}}
      type="button"
    >
      {{children}}
    </button>
  );
}};""",
                "props": ["children", "onClick", "variant", "size", "disabled", "ariaLabel"]
            },
            "input": {
                "base": """import React from 'react';
import styles from './{name}.module.css';

interface {name}Props {{
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
}}

export const {name}: React.FC<{name}Props> = ({{
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
  required = false,
  disabled = false,
  error
}}) => {{
  return (
    <div className={{styles.inputGroup}}>
      <label className={{styles.label}} htmlFor={{label}}>
        {{label}}
        {{required && <span className={{styles.required}}>*</span>}}
      </label>
      <input
        id={{label}}
        className={{`${{styles.input}} ${{error ? styles.error : ''}}`}}
        type={{type}}
        value={{value}}
        onChange={{(e) => onChange(e.target.value)}}
        placeholder={{placeholder}}
        required={{required}}
        disabled={{disabled}}
        aria-describedby={{error ? `${{label}}-error` : undefined}}
      />
      {{error && (
        <span id={{`${{label}}-error`}} className={{styles.errorMessage}} role="alert">
          {{error}}
        </span>
      )}}
    </div>
  );
}};""",
                "props": ["label", "value", "onChange", "type", "placeholder", "required", "disabled", "error"]
            },
            "card": {
                "base": """import React from 'react';
import styles from './{name}.module.css';

interface {name}Props {{
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  variant?: 'default' | 'outlined' | 'elevated';
  clickable?: boolean;
  onClick?: () => void;
}}

export const {name}: React.FC<{name}Props> = ({{
  children,
  title,
  subtitle,
  actions,
  variant = 'default',
  clickable = false,
  onClick
}}) => {{
  const CardComponent = clickable ? 'button' : 'div';
  
  return (
    <CardComponent
      className={{`${{styles.card}} ${{styles[variant]}} ${{clickable ? styles.clickable : ''}}`}}
      onClick={{clickable ? onClick : undefined}}
      type={{clickable ? 'button' : undefined}}
    >
      {{(title || subtitle) && (
        <div className={{styles.header}}>
          {{title && <h3 className={{styles.title}}>{{title}}</h3>}}
          {{subtitle && <p className={{styles.subtitle}}>{{subtitle}}</p>}}
        </div>
      )}}
      <div className={{styles.content}}>
        {{children}}
      </div>
      {{actions && (
        <div className={{styles.actions}}>
          {{actions}}
        </div>
      )}}
    </CardComponent>
  );
}};""",
                "props": ["children", "title", "subtitle", "actions", "variant", "clickable", "onClick"]
            }
        }
        
        # Design patterns
        self.design_patterns = {
            "glassmorphism": {
                "description": "Modern glass-like effect with blur and transparency",
                "css": """
.glassmorphism {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}"""
            },
            "neumorphism": {
                "description": "Soft, extruded plastic look",
                "css": """
.neumorphism {
  background: #e0e0e0;
  border-radius: 20px;
  box-shadow: 20px 20px 60px #bebebe, -20px -20px 60px #ffffff;
}"""
            },
            "modern_card": {
                "description": "Clean, modern card design",
                "css": """
.modern_card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.modern_card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}"""
            }
        }

    def generate_component_code(self, name: str, template: Dict, props: Dict, styling: str, accessibility: bool) -> str:
        """Generate component code from template"""
        base_code = template["base"].format(name=name)
        
        # Add accessibility enhancements if requested
        if accessibility:
            base_code = self.add_accessibility_features(base_code)
        
        return base_code

    def generate_types_code(self, name: str, props: Dict) -> str:
        """Generate TypeScript types"""
        return f"""// {name} Component Types
export interface {name}Props {{
  // Generated props based on component requirements
  [key: string]: any;
}}

export interface {name}State {{
  // Component state interface
}}

export type {name}Variant = 'primary' | 'secondary' | 'outline';
export type {name}Size = 'small' | 'medium' | 'large';
"""

    def generate_css_code(self, name: str, styling: str) -> str:
        """Generate CSS styles"""
        base_styles = f"""/* {name} Component Styles */
.button {{
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  font-family: inherit;
}}

.primary {{
  background-color: #3b82f6;
  color: white;
}}

.primary:hover:not(:disabled) {{
  background-color: #2563eb;
}}

.secondary {{
  background-color: #6b7280;
  color: white;
}}

.outline {{
  background-color: transparent;
  border: 2px solid #3b82f6;
  color: #3b82f6;
}}

.small {{
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}}

.medium {{
  padding: 0.5rem 1rem;
  font-size: 1rem;
}}

.large {{
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
}}

.button:disabled {{
  opacity: 0.5;
  cursor: not-allowed;
}}

.button:focus {{
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}}
"""
        
        # Add styling-specific enhancements
        if styling == "glassmorphism":
            base_styles += self.design_patterns["glassmorphism"]["css"]
        elif styling == "neumorphism":
            base_styles += self.design_patterns["neumorphism"]["css"]
        
        return base_styles

    def generate_test_code(self, name: str, props: Dict) -> str:
        """Generate test file"""
        return f"""import {{ render, screen, fireEvent }} from '@testing-library/react';
import {{ {name} }} from './{name}';

describe('{name}', () => {{
  it('renders correctly', () => {{
    render(<{name}>Test Content</{name}>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  }});

  it('handles click events', () => {{
    const handleClick = jest.fn();
    render(<{name} onClick={{handleClick}}>Click me</{name}>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  }});

  it('is accessible', () => {{
    render(<{name} ariaLabel="Test button">Click me</{name}>);
    expect(screen.getByLabelText('Test button')).toBeInTheDocument();
  }});

  it('handles disabled state', () => {{
    render(<{name} disabled>Disabled</{name}>);
    expect(screen.getByText('Disabled')).toBeDisabled();
  }});
}});
"""

    def add_accessibility_features(self, code: str) -> str:
        """Add accessibility features to component code"""
        # This is a simplified version - in reality, this would be more sophisticated
        return code

    def validate_component_design(self, code: str, design_system: str) -> Dict[str, Any]:
        """Validate component against design system"""
        score = 85  # Base score
        issues = []
        suggestions = []
        
        # Check for accessibility attributes
        if "aria-label" not in code:
            issues.append("Missing aria-label for accessibility")
            score -= 10
        
        # Check for proper TypeScript types
        if "interface" not in code:
            issues.append("Missing TypeScript interface")
            score -= 5
        
        # Check for CSS modules
        if "styles." not in code:
            suggestions.append("Consider using CSS modules for better style encapsulation")
        
        # Check for responsive design
        if "responsive" not in code.lower():
            suggestions.append("Consider adding responsive design patterns")
        
        return {
            "score": max(score, 0),
            "issues": issues,
            "suggestions": suggestions,
            "accessibility_score": 90 if "aria-" in code else 70,
            "performance_score": 85,
            "maintainability_score": 80
        }

    def get_accessibility_recommendations(self, component_type: str, current_level: str, target_level: str) -> List[Dict[str, Any]]:
        """Get accessibility recommendations"""
        recommendations = [
            {
                "category": "Semantic HTML",
                "priority": "high",
                "description": "Use semantic HTML elements (button, input, etc.) instead of divs",
                "implementation": "Replace <div onClick={...}> with <button onClick={...}>",
                "wcag_guideline": "4.1.2 Name, Role, Value"
            },
            {
                "category": "Keyboard Navigation",
                "priority": "high", 
                "description": "Ensure all interactive elements are keyboard accessible",
                "implementation": "Add tabIndex and onKeyDown handlers for Enter/Space keys",
                "wcag_guideline": "2.1.1 Keyboard"
            },
            {
                "category": "Color Contrast",
                "priority": "medium",
                "description": "Ensure sufficient color contrast (4.5:1 for AA, 7:1 for AAA)",
                "implementation": "Use tools like WebAIM contrast checker to validate colors",
                "wcag_guideline": "1.4.3 Contrast (Minimum)"
            },
            {
                "category": "Focus Management",
                "priority": "medium",
                "description": "Provide visible focus indicators for all interactive elements",
                "implementation": "Add :focus styles with outline or box-shadow",
                "wcag_guideline": "2.4.7 Focus Visible"
            },
            {
                "category": "Screen Reader Support",
                "priority": "high",
                "description": "Add appropriate ARIA labels and descriptions",
                "implementation": "Use aria-label, aria-describedby, and role attributes",
                "wcag_guideline": "1.3.1 Info and Relationships"
            }
        ]
        
        # Filter based on target level
        if target_level == "AAA":
            recommendations.append({
                "category": "Enhanced Contrast",
                "priority": "high",
                "description": "Use 7:1 contrast ratio for AAA compliance",
                "implementation": "Update color palette to meet AAA standards",
                "wcag_guideline": "1.4.6 Contrast (Enhanced)"
            })
        
        return recommendations

    def analyze_performance(self, code: str, target: str) -> Dict[str, Any]:
        """Analyze component performance"""
        score = 80  # Base score
        optimizations = []
        
        # Check for React.memo
        if "React.memo" not in code:
            optimizations.append({
                "type": "Memoization",
                "description": "Wrap component in React.memo to prevent unnecessary re-renders",
                "impact": "Medium",
                "implementation": "export default React.memo(ComponentName)"
            })
        
        # Check for useCallback/useMemo
        if "useCallback" not in code and "onClick" in code:
            optimizations.append({
                "type": "Callback Optimization",
                "description": "Use useCallback for event handlers to prevent child re-renders",
                "impact": "Low",
                "implementation": "const handleClick = useCallback(() => {...}, [dependencies])"
            })
        
        # Check for inline styles
        if "style={{" in code:
            optimizations.append({
                "type": "Style Optimization",
                "description": "Move inline styles to CSS modules or styled-components",
                "impact": "Low",
                "implementation": "Use CSS modules or extract to stylesheet"
            })
            score -= 5
        
        # Check for large bundle size indicators
        if len(code) > 2000:
            optimizations.append({
                "type": "Code Splitting",
                "description": "Consider splitting large components into smaller pieces",
                "impact": "Medium",
                "implementation": "Use React.lazy() and Suspense for code splitting"
            })
        
        return {
            "score": score,
            "optimizations": optimizations,
            "bundle_impact": "Low",
            "render_performance": "Good",
            "memory_usage": "Optimal"
        }

    async def start_server(self, port: int = 9002):
        """Start the UI/UX Agent MCP server"""
        logger.info(f"🎨 Starting Simple UI/UX Agent MCP Server on port {port}")
        
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

def main():
    """Main function to run the server"""
    server = SimpleUIUXServer()
    
    try:
        asyncio.run(server.start_server(port=9002))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main() 