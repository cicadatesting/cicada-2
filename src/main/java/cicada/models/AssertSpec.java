package cicada.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;

@JsonIgnoreProperties(ignoreUnknown = true)
public class AssertSpec {
    @JsonProperty("type")
    private String type;

    @JsonProperty("parameters")
    private JsonNode parameters;

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public JsonNode getParameters() {
        return parameters;
    }

    public void setParameters(JsonNode parameters) {
        // try {
        //     ObjectMapper m = new ObjectMapper();
        //     System.out.println(m.writeValueAsString(parameters));
        // } catch (Exception e) {
        //     System.out.println(e);
        // }
        this.parameters = parameters;
    }
}
