package net.sourceforge.pmd.lang.java.rule.errorprone;


import net.sourceforge.framework.lang.java.rule.AbstractJavaRulechainRule;
import net.sourceforge.framework.lang.java.ast. *;
import net.sourceforge.framework.lang.java.ast.internal. *;
import net.sourceforge.framework.lang.java.types. *;
import net.sourceforge.framework.lang.java.symbols. *;
import net.sourceforge.framework.lang.ast.NodeStream;
public class AvoidUsingOctalValuesRule extends AbstractJavaRulechainRule {
    public AvoidUsingOctalValuesRule() {
        super(ASTNumericLiteral.class);
    }
    
    @Override
    public Object visit(ASTNumericLiteral node, Object data) {
        if (node.isIntegerLiteral() && node.getBase() == 8) {
            addViolation(data, node);
        }
        return data;
    }
}