import praw
import time

# variables

subreddit_list = ['xxx']

# initiate praw

r = praw.Reddit(user_agent='xxx')
r.login('xxx', 'xxx', disable_warning=True)

Errors = praw.errors.HTTPException
NotFound = praw.errors.NotFound

#initate log

log = {}
for s in subreddit_list:
    log[s] = []

#watch for domain spam

while True:
    
    try:

        for subreddit in subreddit_list:
            
            # retrieve domains
            
            get_subreddit = r.get_subreddit(subreddit).get_new(limit=20)
            submissions = (x for x in get_subreddit if x.is_self is False)
            
            for submission in submissions:
                
                if str(submission.id) in log[subreddit]:
                    continue
                
                domain = str(submission.domain)
                author = str(submission.author)
                
                print('--- checking user: ' + author + ' ---')
                print('domain submitted: ' + domain)
                
                domain_submission_listing = r.get_domain_listing(domain, limit=501)
                domain_submission_listing = [x for x in domain_submission_listing]
                domain_authors = [str(x.author) for x in domain_submission_listing]
                
                submission_number = len(domain_submission_listing)
            
                if submission_number <= 500:
                    print(domain + ' has been submitted ' + str(submission_number) + ' times')
                
                unique_authors = len(set(domain_authors))
                
                if submission_number <= 500 and submission_number > 0:
                    
                    #user submitting too often
                    
                    user_ratio = float(domain_authors.count(author)) / float(submission_number)
                    
                    ratio = str(int((user_ratio * 100))) + '%'
                    print('user ratio: ' + ratio)
                    
                    if user_ratio >= float(0.75) and submission_number >= 3 and submission_number <= 5:
                        print('***REPORTED***, ' + domain + ' commonly submitted by user: ' + ratio)
                        report_reason = 'domain mostly submitted by user: ' + ratio
                        submission.report(reason=report_reason)
                        continue
                    if user_ratio >= float(0.65) and submission_number > 5 and submission_number <= 10:
                        print('***REPORTED***, ' + domain + ' commonly submitted by user: ' + ratio)
                        report_reason = 'domain mostly submitted by user: ' + ratio
                        submission.report(reason=report_reason)
                        continue
                    if user_ratio >= float(0.20) and submission_number > 10:
                        print('***REPORTED***, ' + domain + ' commonly submitted by user: ' + ratio)
                        report_reason = 'domain mostly submitted by user: ' + ratio
                        submission.report(reason=report_reason)
                        continue
                    
                    #many shadow banned accounts
            
                    sb_user_count = int(0)        
                    
                    for submission in domain_submission_listing:
                        try:
                            author = str(submission.author.fullname)
                        except NotFound:
                            sb_user_count += 1
                    
                    sb_ratio = float(sb_user_count) / float(unique_authors)
                    print('shadow banned users: ' + str(sb_user_count))
                    if sb_ratio >= float(0.15):
                        print('***REPORTED***, ' + domain + ' has many shadow banned users')
                        sb_user_ratio = str(int(sb_ratio * 100)) + '%'
                        report_reason = 'domain has many shadow banned or deleted users: ' + str(sb_user_count)
                        submission.report(reason=report_reason)
                        continue
                    
                    #few unique accounts
                    
                    print('unique users: ' + str(unique_authors)) 
                    
                    if submission_number >= 10 and unique_authors <= 3:
                        print('***REPORTED***, ' + domain + ' has few unique submitters')
                        report_reason = 'domain has few unique submitters: ' + str(unique_authors)
                        submission.report(reason=report_reason)
                        continue
                
                elif submission_number > 500:       
                    print(domain + ' is commonly submitted')
                    continue
                
                if str(submission.id) not in log[subreddit]:
                    log[subreddit].append(str(submission.id))
                    
                    while True:
                        if len(log[subreddit]) <= 100:
                            break
                        elif len(log[subreddit]) > 100:
                            log_contents = log[subreddit]
                            del log_contents[0]
                            log[subreddit] = log_contents
                
        time.sleep(30)
                    
    except Errors:
        time.sleep(60)
    
    except Exception:
        time.sleep(60)