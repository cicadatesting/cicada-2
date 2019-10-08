package cicada;

import java.util.List;

import com.fasterxml.jackson.databind.JsonNode;

import cicada.models.CicadaClient;

public class Client {
    private CicadaClient cicadaClient;
    private List<JsonNode> actions;
    private int index = 0;

    public Client(CicadaClient cicadaClient, List<JsonNode> actions) {
        this.cicadaClient = cicadaClient;
        this.actions = actions;
    }

    private JsonNode getCurrentAction() {
        // TODO: jinja format action
        JsonNode action = this.actions.get(this.index);
        this.index = (this.index + 1) % this.actions.size();
        return action;
    }

    public JsonNode invoke() {
        // provide client with current action
        return this.cicadaClient.invoke(this.getCurrentAction());
    }
}
