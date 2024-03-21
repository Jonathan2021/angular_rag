import { ThemeProvider } from '@mui/material';
import ChatView from '../views/ChatView';
import { theme } from './theme';

export const App = () => (
    <ThemeProvider theme={theme}>
        <ChatView />
    </ThemeProvider>
);

export default App;