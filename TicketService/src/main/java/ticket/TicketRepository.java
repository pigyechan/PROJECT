package ticket;

public interface TicketRepository {

    Ticket findById(long id);

    void save(Ticket ticket);
}
