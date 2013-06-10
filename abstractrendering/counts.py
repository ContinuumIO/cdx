import ar

######## Aggregators ########
def count(x):
  if type(x) is list: 
    return len(x) 
  if type(x) is None: 
    return 0
  return 1


######## Transfers ##########
def segment(high, low, divider):
  def gen(aggs):
    (min,max) = minmax(aggs)
    def f(v):
      if (v >= ((max-min)/float(divider))):
          return high
      return low
    return f
  return gen


def hdalpha(low, high):
  def gen(aggs):
    (min,max) = minmax(aggs)
    def f(v):
      return interpolatecolors(low,high,min,max,v)
      


###### Other utilities ########

def minmax(aggs):
  return (min(aggs.values), max(aggs.values))

def interpolateColors(low, high, min,  max, v):
  """low--Color for the lowest position
     high-- Color for the highest position
     min -- Smallest value v will take
     max -- largest value v will take
     v -- current value
  """

  if (v>max): v=max
  if (v<min): v=min
  distance = 1-((max-v)/float(max-min));
  r = int(weightedAverage(high.r, low.r, distance))
  g = int(weightedAverage(high.g, low.g, distance))
  b = int(weightedAverage(high.b, low.b, distance))
  a = int(weightedAverage(high.a, low.a, distance))
  return Color(r,g,b,a);


#TODO: Look at the inMens perceptually-weighted average
def weightedAverage(v1, v2, weight): return (v1 -v2) * weight + v2
