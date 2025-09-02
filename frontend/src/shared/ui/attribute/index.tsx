import { AttributForm } from "./form"
import { AttributeList } from "./list"

const Attribute = ({ children }: { children: React.ReactNode }) => <>{children}</>

Attribute.Form = AttributForm
Attribute.List = AttributeList

export { Attribute }
