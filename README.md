# flask_ldr  
flask interface sitting in front of an LDR  
  
## Example interactions:  
  
### GET:  
#### curl http://IP:PORT/ldr_time  
{"0":{"time":2.28,"timeout":false},"1":{"time":2.35,"timeout":false},"2":{"time":2.37,"timeout":false},"average":2.33}  
  
### POST:  
#### curl -X POST -H "Content-Type: application/json" -d '{"iterations": 2, "average_results": false}' http://IP:PORT/ldr_time  
{"0":{"time":2.24,"timeout":false},"1":{"time":2.36,"timeout":false}}  
  
### Supported post args:  
"iterations": {"type": "integer"}  
"io_order": {"type": "integer"}  
"average_results": {"type": "boolean"}  
"stop_on_timeout": {"type": "boolean"}  
