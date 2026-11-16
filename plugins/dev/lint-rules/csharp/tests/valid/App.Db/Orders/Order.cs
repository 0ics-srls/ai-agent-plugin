namespace App.Db.Orders;
public class Order {
    public required string Number { get; set; }
    public int CustomerId { get; set; }
    public Customer Customer { get; set; } = null!;
}
