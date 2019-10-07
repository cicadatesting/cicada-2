package cicada.models;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Test {
    @JsonProperty("name")
    private String name;

    @JsonProperty("clients")
    private List<ClientSpec> clients;

    @JsonProperty("asserts")
    private List<AssertSpec> asserts;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<ClientSpec> getClients() {
        return clients;
    }

    public void setClients(List<ClientSpec> clients) {
        this.clients = clients;
    }

    public List<AssertSpec> getAsserts() {
        return asserts;
    }

    public void setAsserts(List<AssertSpec> asserts) {
        this.asserts = asserts;
    }
}
