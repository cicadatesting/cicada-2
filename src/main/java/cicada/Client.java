package cicada;

import com.fasterxml.jackson.databind.JsonNode;

public interface Client {
    public void readSettings(JsonNode settings);
}