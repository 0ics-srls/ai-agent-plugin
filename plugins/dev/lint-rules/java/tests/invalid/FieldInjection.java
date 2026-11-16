package app;
import org.springframework.beans.factory.annotation.Autowired;
public class FieldInjection {
    @Autowired
    private UserRepository repo;
}
