package app;
public class CleanService {
    private static final Logger logger = LoggerFactory.getLogger(CleanService.class);
    void run() {
        logger.debug("doing");
        future.thenApply(p -> p.name());
    }
}
