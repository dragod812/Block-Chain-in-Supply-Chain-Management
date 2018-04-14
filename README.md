# Block-Chain-in-Supply-Chain-Management
A flask application created to make any supply chain **secure** and **traceable** through the use of a **decentralized blockchain**.
<br>
So we have a supplier and manufacture that we run on different servers. They can Request Goods, Send Goods, Recieve Goods,
Send Payment and Recieve Payment.<br> 
All these transactions create a hash for each of the data involved in the transaction. This hash is sent to all the validators, which
are also servers running on different machines. when the validator has all the hashes and the <br>
**requested_hash = sent_hash = recieved_hash** <br>
and <br>
**requested_payment = sent_payment = recieved_payment**.<br>
We understand that the transaction was successful and any of the validators can
mine this new_transaction to create a block in the block chain. The other validators can call the consensus to update their blockchains
, which follows the **longest chain rule**.<br>
We can see the entire blockchain by sending a get request to the validators. I used postman to send post and get requests to get the blockchain and call the consensus.
