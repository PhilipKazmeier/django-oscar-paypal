from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

from paypal.express import set_txn, get_txn, do_txn, PayPalError, SALE


def get_paypal_url(basket, user=None, host=None, scheme='https'):
    """
    Return the URL for PayPal Express transaction.

    This involves registering the txn with PayPal to get a one-time
    URL.
    """
    currency = getattr(settings, 'PAYPAL_CURRENCY', 'GBP')
    if host is None:
        host = Site.objects.get_current().domain
    return_url = '%s://%s%s' % (scheme, host, reverse('paypal-success-response'))
    cancel_url = '%s://%s%s' % (scheme, host, reverse('paypal-cancel-response'))

    # PayPal supports 3 actions: 'Sale', 'Authorization', 'Order'
    action = getattr(settings, 'PAYPAL_PAYMENT_ACTION', SALE)

    # Pass a default billing address is there is one
    address = None
    if user:
        addresses = user.addresses.all().order_by('-is_default_for_billing')
        if len(addresses):
            address = addresses[0]
    return set_txn(basket=basket,
                   currency=currency,
                   return_url=return_url,
                   cancel_url=cancel_url,
                   action=action,
                   user=user,
                   address=address)


def fetch_transaction_details(token):
    """
    Fetch the completed details about the PayPal transaction.
    """
    return get_txn(token)


def complete(payer_id, token, amount, currency):
    """
    Confirm the payment action.
    """
    action = getattr(settings, 'PAYPAL_PAYMENT_ACTION', SALE)
    return do_txn(payer_id, token, amount, currency, action=action)

