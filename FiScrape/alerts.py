from scrapy.utils.project import get_project_settings
from scrapy.mail import MailSender
# from email.mime.text import MIMEText

mailer = MailSender.from_settings(get_project_settings())

# mailer = MailSender(mailfrom="pwenewsalerts@gmail.com", smtphost="smtp.gmail.com", smtpssl=True, smtptls=False,
#                     smtpport=465, smtpuser="pwenewsalerts@gmail.com", smtppass="pwecapitalnewsalerts123$")
  
body_of_email = 'A new article was published about...'
# msg = MIMEText(body_of_email, 'html')
msg = body_of_email

async def spider_closed():
    await mailer.send(to=["saran.c@pwecapital.com"], subject="PWE News Alert", body=msg, mimetype='text/plain')  # cc=["another@example.com" charset='utf-8'

spider_closed()


# import smtplib
# from email.mime.text import MIMEText

# sender = "pwenewsalerts@gmail.com"
# receivers = ["saran.c@pwecapital.com"]
# body_of_email = 'A new article was published about...'
# msg = MIMEText(body_of_email, 'html')
# msg['Subject'] = 'PWE News Alert'
# msg['From'] = sender
# msg['To'] = ','.join(receivers)

# s = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
# s.login(user = 'pwenewsalerts@gmail.com', password = 'pwecapitalnewsalerts123$')
# s.sendmail(sender, receivers, msg.as_string())
# s.quit()


# class SendEmailPipeLine(object):
#     def __init__(self, settings):
#         self.mailer = MailSender.from_settings(settings)
#         # self.pools = []

#     @classmethod
#     def from_crawler(cls, crawler):
#         settings = crawler.settings
#         return cls(settings)

#     # def process_item(self, item, spider):
#     #     self.pools.append(item)
#     #     return item

#     # def close_spider(self, spider):
#     #     self.mailer.send(to=["saran.c@pwecapital.com"], subject="PWE News Alert", body='A new article was published about...', mimetype='text/plain')  # cc=["another@example.com" charset='utf-8'

#     async def finish_scraping(self, spider, crawler):
#         await engine_stopped()
#         return self.send_email()

#     def send_email(self):
#         return self.mailer.send(to=["saran.c@pwecapital.com"], subject="PWE News Alert", body='A new article was published about...', mimetype='text/plain')  # cc=["another@example.com" charset='utf-8'

#     # async def close_spider(self):
#     #     if engine_stopped():
#     #         await self.mailer.send(to=["saran.c@pwecapital.com"], subject="PWE News Alert", body='A new article was published about...', mimetype='text/plain')  # cc=["another@example.com" charset='utf-8'
#     #         return


# class SendEmailPipeLine(object):

#     def __init__(self, settings):
#         """
#         Sends an email notification for each new article.
#         """
#         engine = db_connect()
#         create_table(engine)
#         self.Session = sessionmaker(bind=engine)
#         self.mailer = MailSender.from_settings(settings)
#         logging.info("****SendEmailPipeLine: database connected****")

#     @classmethod
#     def from_crawler(cls, crawler):
#         settings = crawler.settings
#         return cls(settings)

#     def process_item(self, item, spider):
#         if isinstance(item, TestItem):
#             return item
#         else:
#             return self.check_send_email(item)

#     def check_send_email(self, item):
#         session = self.Session()
#         exist_article = session.query(Article).filter_by(article_link=item["article_link"]).first()
#         session.close()
#         if exist_article is None:  # the current article exists
#             return self.send_email(item)

#     def send_email(self, item):
#         headline = item["headline"]
#         print ('EMAIL HEADLINE:', headline)
#         subject = "News Alert: " + headline
#         standfirst = item["standfirst"]
#         article_link = item["article_link"]
#         email_body = standfirst + '\n' + article_link
#         return self.mailer.send(to=["saran.c@pwecapital.com"], subject=subject, body=email_body, mimetype='text/plain')  # cc=["another@example.com" charset='utf-8'
