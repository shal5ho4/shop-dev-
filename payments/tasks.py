from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order

from io import BytesIO
from celery import task
import weasyprint


@task
def payment_completed(order_id):

  order = Order.objects.get(id=order_id)

  subject = f'My shop - EE Invoice no.{order.id}'
  message = 'Please find the attached invoice for your recent purchase.'
  email = EmailMessage(subject, message, 
                        settings.EMAIL_HOST_USER, [order.email])

  html = render_to_string('admin/orders/order/pdf.html', {'order': order})
  out = BytesIO()
  stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
  weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

  email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
  email.send()

