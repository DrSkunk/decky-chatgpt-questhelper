import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  TextField,
  staticClasses
} from "@decky/ui";
import {
  callable,
  definePlugin,
  toaster,
} from "@decky/api"
import { useState, useEffect } from "react";
import { FaQuestionCircle } from "react-icons/fa";

// Define the response type from the backend
interface QuestHelpResponse {
  success: boolean;
  help_text?: string;
  error?: string;
}

// Callable functions for the backend
const requestQuestHelp = callable<[], QuestHelpResponse>("request_quest_help");
const setApiKey = callable<[apiKey: string], boolean>("set_api_key");
const getApiKey = callable<[], string>("get_api_key");

function Content() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [helpText, setHelpText] = useState<string>("");
  const [apiKey, setApiKeyState] = useState<string>("");
  const [hasApiKey, setHasApiKey] = useState<boolean>(false);

  // Load API key on mount
  useEffect(() => {
    const loadApiKey = async () => {
      try {
        const key = await getApiKey();
        if (key && key.length > 0) {
          setApiKeyState(key);
          setHasApiKey(true);
        }
      } catch (error) {
        console.error("Failed to load API key:", error);
      }
    };
    loadApiKey();
  }, []);

  const handleQuestHelp = async () => {
    setIsLoading(true);
    setHelpText("");
    
    try {
      const response = await requestQuestHelp();
      
      if (response.success && response.help_text) {
        setHelpText(response.help_text);
        toaster.toast({
          title: "Quest Help Received!",
          body: "Check the plugin for guidance."
        });
      } else {
        const errorMsg = response.error || "Unknown error occurred";
        setHelpText(`Error: ${errorMsg}`);
        toaster.toast({
          title: "Quest Help Failed",
          body: errorMsg
        });
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      setHelpText(`Error: ${errorMsg}`);
      toaster.toast({
        title: "Quest Help Failed",
        body: errorMsg
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveApiKey = async () => {
    if (!apiKey || apiKey.trim().length === 0) {
      toaster.toast({
        title: "Invalid API Key",
        body: "Please enter a valid OpenAI API key"
      });
      return;
    }

    try {
      const success = await setApiKey(apiKey.trim());
      if (success) {
        setHasApiKey(true);
        toaster.toast({
          title: "API Key Saved",
          body: "Your OpenAI API key has been saved successfully"
        });
      } else {
        toaster.toast({
          title: "Failed to Save",
          body: "Could not save the API key"
        });
      }
    } catch (error) {
      toaster.toast({
        title: "Error",
        body: "Failed to save API key"
      });
    }
  };

  return (
    <>
      <PanelSection title="Settings">
        <PanelSectionRow>
          <TextField
            label="OpenAI API Key"
            value={apiKey}
            onChange={(e) => setApiKeyState(e.target.value)}
          />
        </PanelSectionRow>
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={handleSaveApiKey}
            disabled={!apiKey || apiKey.trim().length === 0}
          >
            Save API Key
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>

      <PanelSection title="Quest Helper">
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={handleQuestHelp}
            disabled={!hasApiKey || isLoading}
          >
            {isLoading ? "Analyzing..." : "Get Help with Quest"}
          </ButtonItem>
        </PanelSectionRow>
        
        {helpText && (
          <PanelSectionRow>
            <div style={{ 
              padding: "10px", 
              backgroundColor: "rgba(0, 0, 0, 0.3)", 
              borderRadius: "5px",
              whiteSpace: "pre-wrap",
              wordWrap: "break-word",
              maxHeight: "300px",
              overflowY: "auto"
            }}>
              {helpText}
            </div>
          </PanelSectionRow>
        )}
        
        {!hasApiKey && (
          <PanelSectionRow>
            <div style={{ 
              padding: "10px", 
              color: "#ff6b6b",
              fontSize: "0.9em"
            }}>
              ⚠️ Please configure your OpenAI API key in Settings first
            </div>
          </PanelSectionRow>
        )}
      </PanelSection>
    </>
  );
};

export default definePlugin(() => {
  console.log("ChatGPT Quest Helper plugin initializing")

  return {
    // The name shown in various decky menus
    name: "Quest Helper",
    // The element displayed at the top of your plugin's menu
    titleView: <div className={staticClasses.Title}>ChatGPT Quest Helper</div>,
    // The content of your plugin's menu
    content: <Content />,
    // The icon displayed in the plugin list
    icon: <FaQuestionCircle />,
    // The function triggered when your plugin unloads
    onDismount() {
      console.log("ChatGPT Quest Helper unloading")
    },
  };
});
