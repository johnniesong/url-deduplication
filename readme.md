# 简介
通过对url中的路径和参数进行归一化替换,实现更好的url去重
本项目是参考crawlergo项目中的去重逻辑实现

# 参考
crawlergo: https://github.com/Qianlitp/crawlergo

# 归一化举例
1. TimeMark = "{{time}}" 对应正则 re.compile(r"-|:|\s")
2. BoolMark = "{{bool}}" 对应检查函数             
`if isinstance(value, bool):
                marked_param_map[key] = BoolMark
                continue`

对每一条url进行各种格式检查,将符合正则或检查函数的位置替换为对应的归一化模版,如{{time}}.  
全部处理后,再进行去重,对于大量不规则的url去重效果较好.基本为主流做法.

当然这是基于专家规则的实现方案,比较通用.  
如果想对某个正则不好描述的复杂参数进行特制化去重,可以使用机器学习的方法,比如svm,决策树基于样本练个小模型.
### 举例:
原始url  
a.com/111111?time=2023-12-25  
a.com/222222?time=2023-12-22

中间处理结果  
a.com/{{number}}?time={{time}}  
a.com/{{number}}?time={{time}}

去重后保留  
a.com/111111?time=2023-12-25
