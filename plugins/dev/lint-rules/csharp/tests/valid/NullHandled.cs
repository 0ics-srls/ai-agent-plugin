namespace App;
public class Handled {
    public int Length(string? s) => s?.Length ?? 0;
    public bool Differs(int a, int b) => a != b && !IsEmpty(a);
    public Customer Load(Customer? found) => found ?? throw new InvalidOperationException("seeded at start");
}
