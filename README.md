# Block-Chain-in-Supply-Chain-Management
A flask application created to make a supply chain secure and traceable through the use of a decentralized blockchain.
<br>
So we have a supplier and manufacture that we run on different servers. They can Request Goods, Send Goods, Recieve Goods,<br>
Send Payment and Recieve Payment.<br> 
All these transactions create a hash for each of the data involved in the transaction. This hash is sent to all the validators, which<br>
are also servers running on different machines. when the validator has all the hashes and the requested_hash = sent_hash = recieved_hash <br>
and requested_payment = sent_payment = recieved_payment, We understand that the transaction was successful and any of the validators can<br>
mine this new_transaction to create a block in the block chain. The other validators can call the consensus to update their blockchains<br>
, which follows the longest chain rule.
