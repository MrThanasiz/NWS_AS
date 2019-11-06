import os
mailset = ["testuser@gmail.com", "testuser@hotmail.com", "testuser@yahoo.com"]
maillist = []
mailid = 0
for mail in mailset:
    if os.path.isdir("emails/" + mail):
        for file in os.listdir("emails/" + mail):
            if file.endswith(".txt"):
                maillist.append([os.path.join("emails/" + mail, file),
                        "ID: " + str(mailid) + " Date - Sender: " + file[:-4] + " Recipient: " + mail])
                mailid = mailid + 1


f = open(maillist[0][0], 'r')
file_contents = f.read()
splt = file_contents.splitlines()
if len(splt) >= 1:
    for i in range(len(splt) - 1):
        self.code250("-" + maillist[i], module)
    self.code250(" " + maillist[-1], module)
else:
    self.code554(", empty mail", module)
print (splt)
f.close()