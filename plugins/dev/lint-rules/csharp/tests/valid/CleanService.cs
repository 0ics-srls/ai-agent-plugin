namespace App;
public class CleanService {
    private string Name { get; set; } = string.Empty;
    public async Task Do(int id, CancellationToken ct) {
        _logger.LogTrace("doing");
        var u = await _repo.GetAsync(id);
        await _context.SaveChangesAsync(ct);
    }
}
