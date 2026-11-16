import java.util.Optional;
import java.util.function.Supplier;

public class OptionalGet {
    int firstOf(Optional<Integer> o, Supplier<Integer> supplier) {
        return o.get() + supplier.get();
    }
}
