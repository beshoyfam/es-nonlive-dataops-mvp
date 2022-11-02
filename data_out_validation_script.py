#!/usr/bin/env python
# coding: utf-8

# In[18]:


from google.cloud.storage import Blob
from google.cloud import storage


# In[19]:


client = storage.Client()
bucket = client.bucket('bvertexai')


# In[32]:


blob = bucket.get_blob('sales/sales.csv')


# In[33]:


print(blob.size)


# In[37]:


total_size = 0
for blob in bucket.list_blobs():
    print("Name: "+ blob.name +" Size blob obj: "+str(blob.size) + "bytes")
    total_size += blob.size
    #do something  
print(total_size/1000000)


# In[ ]:




