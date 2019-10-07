package cicada.models;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ClientSpec {
    @JsonProperty("type")
    private String type;

    @JsonProperty("settings")
    private JsonNode settings;

    @JsonProperty("actions")
    private List<JsonNode> actions;

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public JsonNode getSettings() {
        return settings;
    }

    public void setSettings(JsonNode settings) {
        this.settings = settings;
    }

    public List<JsonNode> getActions() {
        return actions;
    }

    public void setActions(List<JsonNode> actions) {
        this.actions = actions;
    }
}
