public class NonTaskResultWait
{
    public string Handle(ParseResult parseResult, SemaphoreSlim semaphoreSlim)
    {
        semaphoreSlim.Wait();
        return parseResult.Result;
    }
}
