namespace App;
public class Qualified {
    public void Do() {
        System.Console.WriteLine("debug");
        global::System.Console.Error.WriteLine("failed");
    }
}
