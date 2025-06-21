import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button.jsx';

describe('Button component', () => {
  it('renders children and responds to click', () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(onClick).toHaveBeenCalled();
  });

  it('shows loader when loading', () => {
    const { container } = render(<Button loading>Load</Button>);
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });
});
