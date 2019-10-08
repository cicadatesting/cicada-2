package cicada.models;

import com.fasterxml.jackson.databind.JsonNode;

public interface CicadaClient {
    public void readSettings(JsonNode settings);

    /**
     * Call client with action formatted with state container
     * @param action formatted information for client to deserialize and run
     * @return results to add to state container
     */
    public JsonNode invoke(JsonNode action);
}