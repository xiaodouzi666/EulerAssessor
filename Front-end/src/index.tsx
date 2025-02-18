import { createRoot } from 'react-dom/client';
import App from './App';

const container = document.getElementById('root');
const root = createRoot(container);
try {
  root.render(<App />);
} catch (error) {
  console.log(error);
}
