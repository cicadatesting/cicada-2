package cicada;

import java.lang.System.Logger;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import cicada.models.AssertSpec;
import cicada.models.ClientSpec;
import cicada.models.Test;

public class TestProcessor {
    Map<String, Class<? extends Client>> availableClients;
    Map<String, Class<? extends Assert>> availableAsserts;

    public TestProcessor() {
        this.availableAsserts = new HashMap<>();
        this.availableAsserts = new HashMap<>();
    }

    public void addClient(String name, Class<? extends Client> client) {
        this.availableClients.put(name, client);
    }

    public void addAssert(String name, Class<? extends Assert> asrt) {
        this.availableAsserts.put(name, asrt);
    }

    public List<Client> makeClients(List<ClientSpec> clientSpecs) {
        List<Client> clients = new ArrayList<>();

        for (ClientSpec clientSpec : clientSpecs) {
            try {
                Client c = this.availableClients.get(clientSpec.getType()).getDeclaredConstructor().newInstance();
                c.readSettings(clientSpec.getSettings());
                clients.add(c);
            } catch (
                NullPointerException
                |InstantiationException
                |IllegalAccessException
                |InvocationTargetException
                |NoSuchMethodException e
            ) {
                // TODO: fail out
                System.out.println(e);
            }
        }

        return clients;
    }

    public List<Assert> makeAsserts(List<AssertSpec> assertSpecs) {
        List<Assert> asserts = new ArrayList<>();

        for (AssertSpec assertSpec : assertSpecs) {
            try {
                Assert a = this.availableAsserts.get(assertSpec.getType()).getDeclaredConstructor().newInstance();
                a.readParameters(assertSpec.getParameters());
                asserts.add(a);
            } catch (
                NullPointerException
                |InstantiationException
                |IllegalAccessException
                |InvocationTargetException
                |NoSuchMethodException e
            ) {
                // TODO: fail out
                System.out.println(e);
            }
        }

        return asserts;
    }

    public void processTest(Test test) {
        // TODO: multi threaded clients
        // TODO: JsonNode -> Jinja -> JsonNode

        List<Client> clients = new ArrayList<>();
        List<Assert> asserts = new ArrayList<>();

        if (test.getClients() != null) {
            clients = makeClients(test.getClients());
        }

        if (test.getAsserts() != null) {
            asserts = makeAsserts(test.getAsserts());
        }

        if (test.getExecutionsPerClient() != null) {
            test.setExecutionsPerClient(asserts.size() > 0 ? Integer.MAX_VALUE : 1);
        }

        // run clients once if no asserts (or number of times specified)
        // run clients indefinitely until asserts pass
    }
}
