import { RouterProvider, createHashRouter } from 'react-router-dom';
import './App.css';

import Layout from './views/layout';
import Migration from './views/migration';
import Environment from './views/environment';
import Software from './views/software';
import Configuration from './views/configuration';
import Compatibility from './views/compatibility';

import ErrorPage from './views/error';

import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from '@tanstack/react-query';
const queryClient = new QueryClient();

const router = createHashRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
      {
        path: '/',
        element: <Migration />,
      },
      {
        path: 'environment',
        element: <Environment />,
      },
      {
        path: 'software',
        element: <Software />,
      },
      {
        path: 'configuration',
        element: <Configuration />,
      },
      {
        path: 'compatibility',
        element: <Compatibility />,
      },
    ],
  },
]);

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}
