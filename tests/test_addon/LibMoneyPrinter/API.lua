-- libmoneyprinter

LibMoneyPrinter = {}

function LibMoneyPrinter.getMoney()
  local copper, silver, gold = GetMoney(), 0, 0
  copper, silver = copper % 100, math.floor(copper / 100)
  silver, gold = silver % 100, math.floor(silver / 100)
  return gold, silver, copper
end
