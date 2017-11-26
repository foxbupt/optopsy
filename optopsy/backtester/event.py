from enum import Enum

EventType = Enum("EventType", "DATA ORDER FILL REJECTED")


class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """

    def __init__(self, event_type, date):
        self.event_type = event_type
        self.date = date

    def print_event(self):
        pass


class DataEvent(Event):

    def __init__(self, date, quotes):
        """
        A Data Event is generated by the data feed when it retrieves latest quotes
        from the data source as called by the option chain iterator. It contains an
        OptionQuery object 'quotes' to be fed into the broker to update pending orders
        and account positions. It is also fed to the strategy to be used to generate trading
        actions.
        :param date: The date of the quotes
        :param quotes: A DataFrame containing option chains for all subscribed symbols
        """

        super().__init__(EventType.DATA, date)
        self.quotes = quotes


class OrderEvent(Event):

    def __init__(self, date, order):
        """
        An Order Event is created by the strategy class to hold an order request
        to be executed by the broker.
        :param date: Date of event
        :param order: Order for the event
        """

        super().__init__(EventType.ORDER, date)
        self.order = order
        print(self)

    def __str__(self):
        return f"ORDER #{self.order.ticket} OPENED ON {self.date}: {self.order}"


class FillEvent(Event):

    def __init__(self, date, order):
        """
        A Fill event is generated by the broker when an order has passed all
        execution checks and executed at the current market price.
        :param date: Date of event
        :param order: Order for the event
        """

        super().__init__(EventType.FILL, date)
        self.order = order
        self.mark = order.mark
        self.ticket = order.ticket
        self.action = order.action
        self.quantity = order.quantity
        self.cost = order.total_cost
        self.margin = order.margin
        self.commission = order.commissions
        print(self)

    def __str__(self):
        return f"ORDER #{self.order.ticket} FILLED ON {self.date}: {self.order}"


class RejectedEvent(Event):
    def __init__(self, date, order):
        """
        A Rejected Event is generated when a newly submitted order does not meet
        the execution criterion such as not enough buying power or cash.
        :param date:
        :param order:
        """
        super().__init__(EventType.REJECTED, date)
        self.order = order
        print(self)

    def __str__(self):
        return f"ORDER #{self.order.ticket} REJECTED ON {self.date}: {self.order}"
