import { ThemeProvider } from "@/components/theme-provider"
import ChatbotUI from "./components/Chatbot"

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <ChatbotUI/>
    </ThemeProvider>
  )
}

export default App
