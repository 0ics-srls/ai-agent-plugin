namespace App;
public class Svc {
    public void Do(int id) {
        var task = _repo.GetAsync(id);
        var u = task.Result;
        task.Wait();
        var user = _service.GetAsync(id).Result;   // csharp-senior_10.md "Never block on a Task"
        _service.SaveAsync().Wait();
    }
}
