import { renderHook, act } from '@testing-library/react';
import { useIsMobile } from './use-mobile';

function setupMatchMedia() {
  let listener = null;
  window.matchMedia = jest.fn().mockImplementation(() => ({
    matches: window.innerWidth < 768,
    addEventListener: (_evt, cb) => { listener = cb; },
    removeEventListener: jest.fn(),
  }));
  return () => listener && listener();
}

describe('useIsMobile', () => {
  it('detects viewport changes', () => {
    window.innerWidth = 1000;
    const trigger = setupMatchMedia();
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);

    act(() => {
      window.innerWidth = 500;
      trigger();
    });
    expect(result.current).toBe(true);
  });
});
