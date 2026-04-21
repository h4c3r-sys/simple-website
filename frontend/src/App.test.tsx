import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders chat app layout elements', () => {
  render(<App />);
  const serverHeader = screen.getByText(/The Sacred Citadel/i);
  expect(serverHeader).toBeInTheDocument();

  const systemMessage = screen.getByText(/Welcome to your secure chat/i);
  expect(systemMessage).toBeInTheDocument();
});
